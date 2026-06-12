from __future__ import annotations

from decimal import Decimal

import httpx
import pytest

from scripts.israeli_e_invoice_compliance_client import (
    ApprovalResponse,
    Environment,
    InvoiceAPIError,
    InvoiceApprovalRequest,
    InvoiceAuthenticationError,
    InvoiceComplianceClient,
    InvoiceValidationError,
    calculate_total_including_vat,
    calculate_vat_amount,
    is_valid_vat_number,
    requires_allocation,
    shortened_allocation_number,
    threshold_for,
)


def sample_request(**overrides):
    payload = {
        "invoice_id": "INV-1",
        "invoice_type": 305,
        "vat_number": 123456782,
        "customer_vat_number": 777777715,
        "customer_name": "Example Customer Ltd",
        "invoice_date": "2026-06-15",
        "invoice_issuance_date": "2026-06-15",
        "accounting_software_number": 123456782,
        "amount_before_discount": "6000.00",
        "discount": "0.00",
        "payment_amount": "6000.00",
        "vat_amount": "1080.00",
        "payment_amount_including_vat": "7080.00",
        "items": [
            {
                "index": 1,
                "description": "Monthly consulting services",
                "quantity": "1",
                "price_per_unit": "6000.00",
                "discount": "0.00",
                "total_amount": "6000.00",
                "vat_rate": "18.00",
                "vat_amount": "1080.00",
            }
        ],
    }
    payload.update(overrides)
    return InvoiceApprovalRequest.from_payload(payload)


def test_valid_vat_number_passes():
    assert is_valid_vat_number("123456782")
    assert is_valid_vat_number(777777715)


def test_invalid_vat_number_fails():
    assert not is_valid_vat_number("123456789")
    assert not is_valid_vat_number("000000000")


def test_threshold_schedule_uses_invoice_date():
    assert threshold_for("2026-06-01") == Decimal("5000.00")
    assert threshold_for("2026-01-15") == Decimal("10000.00")
    assert threshold_for("2025-03-01") == Decimal("20000.00")


def test_requires_allocation_above_june_2026_threshold():
    assert requires_allocation(invoice_type=305, payment_amount="5000.01", invoice_date="2026-06-15")


def test_no_allocation_at_or_below_threshold():
    assert not requires_allocation(invoice_type=305, payment_amount="5000.00", invoice_date="2026-06-15")
    assert not requires_allocation(invoice_type=320, payment_amount="9000.00", invoice_date="2026-06-15")
    assert not requires_allocation(invoice_type=305, payment_amount="9000.00", invoice_date="2026-06-15", israeli_b2b=False)


def test_vat_calculation_rounds_to_agorot():
    assert calculate_vat_amount("6000.00") == Decimal("1080.00")
    assert calculate_total_including_vat("6000.00") == Decimal("7080.00")


def test_sample_request_validates_and_serializes():
    request = sample_request()
    assert request.local_validation_errors() == []
    payload = request.to_api_dict()
    assert payload["vat_number"] == 123456782
    assert payload["customer_vat_number"] == 777777715
    assert payload["payment_amount"] == 6000.0
    assert payload["items"][0]["vat_amount"] == 1080.0


def test_validation_catches_total_mismatch():
    request = sample_request(payment_amount_including_vat="7000.00")
    with pytest.raises(InvoiceValidationError) as excinfo:
        request.raise_for_validation_errors()
    assert "payment_amount_including_vat" in str(excinfo.value)


def test_validation_requires_customer_vat_number_for_above_threshold_b2b():
    request = sample_request(customer_vat_number=None)
    with pytest.raises(InvoiceValidationError) as excinfo:
        request.raise_for_validation_errors()
    assert "customer_vat_number" in str(excinfo.value)


def test_shortened_allocation_number_uses_rightmost_nine_digits():
    assert shortened_allocation_number("20240704061109183186068226") == "186068226"


def test_sync_client_posts_to_sandbox_approval_endpoint():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["auth"] = request.headers.get("Authorization")
        return httpx.Response(200, json={"status": 200, "approved": True, "confirmation_number": "20240704061109183186068226", "message": "OK"})

    client = InvoiceComplianceClient("token", Environment.SANDBOX, transport=httpx.MockTransport(handler))
    response = client.request_approval(sample_request())
    assert response.approved is True
    assert response.confirmation_number.endswith("68226")
    assert seen["url"].endswith("/shaam/tsandbox/Invoices/v2/Approval")
    assert seen["auth"] == "Bearer token"


@pytest.mark.asyncio
async def test_async_client_posts_to_approval_endpoint():
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"status": 200, "approved": True, "confirmation_number": "999999999", "message": "OK"})

    client = InvoiceComplianceClient("token", Environment.SANDBOX, transport=httpx.MockTransport(handler))
    response = await client.async_request_approval(sample_request())
    assert response.approved is True
    assert response.confirmation_number == "999999999"


def test_authentication_error_is_raised_for_401():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"message": "Unauthorized"})

    client = InvoiceComplianceClient("bad", Environment.SANDBOX, transport=httpx.MockTransport(handler))
    with pytest.raises(InvoiceAuthenticationError):
        client.request_approval(sample_request())


def test_multi_approval_payload_summarizes_invoices():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["json"] = request.content.decode()
        return httpx.Response(200, json={"status": 200, "transaction_id": "TX", "message": {"errors": []}})

    client = InvoiceComplianceClient("token", Environment.SANDBOX, transport=httpx.MockTransport(handler))
    result = client.request_multi_approval([sample_request(), sample_request(invoice_id="INV-2")])
    assert result["transaction_id"] == "TX"
    assert '"invoices_amount":2' in captured["json"].replace(" ", "")


def test_approval_response_extracts_errors():
    response = ApprovalResponse.from_payload(
        {"status": 400, "approved": False, "confirmation_number": "0", "message": {"errors": [{"code": 431, "param": "vat_number"}]}}
    )
    assert response.errors[0]["code"] == 431
