from __future__ import annotations

import argparse
import json
import os
from typing import Any, Mapping, Sequence

from payment_gateway_integrator import (
    AsyncIsraeliPaymentOrchestrator,
    Customer,
    GatewayConfig,
    IsraeliPaymentOrchestrator,
    PaymentGatewayError,
    PaymentRequest,
    RefundRequest,
    response_to_dict,
)


def parse_env(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("PGI_ENV", "sandbox"))
    parser.add_argument("--gateway", default=os.getenv("PGI_GATEWAY", "grow"))
    return parser.parse_args(argv)


def env_value(name: str, default: str = "") -> str:
    return os.getenv(name, default)


def endpoint_for(environment: str, gateway: str) -> str:
    specific = os.getenv(f"PGI_ENDPOINT_URL_{environment.upper()}")
    return specific or os.getenv("PGI_ENDPOINT_URL") or f"https://{environment}.example/{gateway}"


def demo_gateway(environment: str, name: str = "grow", **overrides: Any) -> GatewayConfig:
    data = {
        "name": name,
        "endpoint_url": endpoint_for(environment, name),
        "api_key": env_value("PGI_API_KEY", "sandbox-key"),
        "terminal_id": env_value("PGI_TERMINAL_ID", "sandbox-terminal"),
        "secret": env_value("PGI_SECRET", "sandbox-secret"),
        "sandbox": environment == "sandbox",
        "priority": 10,
        "capabilities": {"hosted_checkout", "refund", "partial_refund", "installments", "tokenization", "token_charge", "authorize", "capture"},
        "max_installments": int(env_value("PGI_MAX_INSTALLMENTS", "12")),
        "supported_currencies": {"ILS"},
    }
    data.update(overrides)
    return GatewayConfig(**data)


def demo_request(**overrides: Any) -> PaymentRequest:
    data = {
        "order_id": env_value("PGI_ORDER_ID", "DEMO-0001"),
        "amount_agorot": int(env_value("PGI_AMOUNT_AGOROT", "12500")),
        "currency": env_value("PGI_CURRENCY", "ILS"),
        "description": env_value("PGI_DESCRIPTION", "Demo payment"),
        "customer": Customer(
            name=env_value("PGI_CUSTOMER_NAME", "Dana Levi"),
            email=env_value("PGI_CUSTOMER_EMAIL", "dana@example.co.il"),
            phone=env_value("PGI_CUSTOMER_PHONE", "+972501234567"),
        ),
        "installments": int(env_value("PGI_INSTALLMENTS", "1")),
        "capture": env_value("PGI_CAPTURE", "true").lower() != "false",
        "return_url": env_value("PGI_RETURN_URL", "https://example.co.il/pay/return"),
        "notify_url": env_value("PGI_NOTIFY_URL", "https://example.co.il/pay/callback"),
    }
    data.update(overrides)
    return PaymentRequest(**data)


class FakeTransport:
    def __init__(self, responses: Sequence[Mapping[str, Any]] | None = None, failures: Sequence[Exception] | None = None):
        self.responses = list(responses or [])
        self.failures = list(failures or [])
        self.calls: list[dict[str, Any]] = []

    def __call__(self, method: str, url: str, *, headers: Mapping[str, str], json_body: Mapping[str, Any] | None, timeout: int) -> Mapping[str, Any]:
        self.calls.append({"method": method, "url": url, "headers": dict(headers), "json_body": dict(json_body or {}), "timeout": timeout})
        if self.failures:
            raise self.failures.pop(0)
        return self.responses.pop(0) if self.responses else {"success": True, "transaction_id": "demo", "status": "approved"}


class AsyncFakeTransport(FakeTransport):
    async def __call__(self, method: str, url: str, *, headers: Mapping[str, str], json_body: Mapping[str, Any] | None, timeout: int) -> Mapping[str, Any]:
        return super().__call__(method, url, headers=headers, json_body=json_body, timeout=timeout)


def output(data: Mapping[str, Any]) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


__all__ = [
    "AsyncFakeTransport",
    "AsyncIsraeliPaymentOrchestrator",
    "FakeTransport",
    "IsraeliPaymentOrchestrator",
    "PaymentGatewayError",
    "RefundRequest",
    "demo_gateway",
    "demo_request",
    "output",
    "parse_env",
    "response_to_dict",
]
