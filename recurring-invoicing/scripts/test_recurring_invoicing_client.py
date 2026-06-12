from __future__ import annotations

import json
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from recurring_invoicing import (
    AllocationRequest,
    Customer,
    DocumentType,
    Interval,
    LineItem,
    RecurringInvoiceError,
    RecurringInvoicingClient,
    Subscription,
    SubscriptionStatus,
    add_months,
    build_invoice,
    calculate_totals,
    clean_israeli_tax_id,
    create_shaam_allocation_payload,
    credit_note_for_invoice,
    generate_schedule,
    invoice_from_dict,
    invoice_to_dict,
    is_valid_israeli_tax_id,
    money,
    next_issue_date,
    parse_allocation_response,
    should_request_allocation,
    subscription_from_dict,
    subscription_to_dict,
    threshold_for_issue_date,
    threshold_for_year,
    vat_rate_for_issue_date,
)


def sample_subscription(price: str = "10000.00") -> Subscription:
    return Subscription(
        subscription_id="SUB-100",
        customer=Customer(name="Acme Israel", tax_id="514324995", email="billing@example.co.il"),
        line_items=[LineItem(description="Monthly service", quantity="1", unit_price=price)],
        start_date=date(2026, 1, 31),
        interval=Interval.MONTHLY,
    )


def test_money_rounds_half_up() -> None:
    assert money("10.235") == Decimal("10.24")


def test_vat_rate_before_2025() -> None:
    assert vat_rate_for_issue_date(date(2024, 12, 31)) == Decimal("0.17")


def test_vat_rate_from_2025() -> None:
    assert vat_rate_for_issue_date(date(2025, 1, 1)) == Decimal("0.18")


def test_clean_tax_id_pads_to_nine_digits() -> None:
    assert clean_israeli_tax_id("18") == "000000018"


def test_valid_tax_id_checksum() -> None:
    assert is_valid_israeli_tax_id("514324995") is True


def test_invalid_tax_id_checksum() -> None:
    assert is_valid_israeli_tax_id("514324996") is False


def test_add_months_preserves_month_end() -> None:
    assert add_months(date(2026, 1, 31), 1) == date(2026, 2, 28)


def test_add_months_without_month_end_anchor() -> None:
    assert add_months(date(2026, 1, 30), 1, end_of_month=False) == date(2026, 2, 28)


def test_next_issue_date_quarterly() -> None:
    assert next_issue_date(date(2026, 1, 15), "quarterly") == date(2026, 4, 15)


def test_generate_schedule_count() -> None:
    values = generate_schedule(sample_subscription(), count=3)
    assert values == [date(2026, 1, 31), date(2026, 2, 28), date(2026, 3, 31)]


def test_calculate_totals_with_vat() -> None:
    totals = calculate_totals([LineItem("Service", "2", "100")], date(2026, 6, 1))
    assert totals == {"subtotal": Decimal("200.00"), "vat_amount": Decimal("36.00"), "total": Decimal("236.00")}


def test_calculate_totals_vat_exempt() -> None:
    totals = calculate_totals([LineItem("Export", "1", "100", exempt=True)], date(2026, 6, 1))
    assert totals["vat_amount"] == Decimal("0.00")


def test_validate_subscription_rejects_paused() -> None:
    subscription = sample_subscription()
    subscription.status = SubscriptionStatus.PAUSED
    with pytest.raises(RecurringInvoiceError):
        subscription.validate()


def test_build_invoice_assigns_sequence() -> None:
    invoice = build_invoice(sample_subscription(), date(2026, 1, 31), 7)
    assert invoice.invoice_id == "SUB-100-000007"
    assert invoice.total == Decimal("11800.00")


def test_threshold_for_unknown_year_uses_latest_prior_year() -> None:
    assert threshold_for_year(2029) == Decimal("5000.00")


def test_threshold_for_issue_date_uses_january_2026_threshold() -> None:
    assert threshold_for_issue_date(date(2026, 1, 1)) == Decimal("10000.00")


def test_threshold_for_issue_date_uses_june_2026_threshold() -> None:
    assert threshold_for_issue_date(date(2026, 6, 1)) == Decimal("5000.00")


def test_should_request_allocation_for_large_tax_invoice() -> None:
    invoice = build_invoice(sample_subscription("10000.00"), date(2026, 1, 31), 1)
    assert should_request_allocation(invoice, "000000018") is True


def test_should_not_request_allocation_below_threshold() -> None:
    invoice = build_invoice(sample_subscription("9999.99"), date(2026, 1, 31), 1)
    assert should_request_allocation(invoice, "000000018") is False


def test_should_request_allocation_after_june_2026_lower_threshold() -> None:
    invoice = build_invoice(sample_subscription("5000.00"), date(2026, 6, 1), 1)
    assert should_request_allocation(invoice, "000000018") is True


def test_should_not_request_allocation_below_june_2026_threshold() -> None:
    invoice = build_invoice(sample_subscription("4999.99"), date(2026, 6, 1), 1)
    assert should_request_allocation(invoice, "000000018") is False


def test_should_not_request_allocation_for_receipt() -> None:
    subscription = sample_subscription("30000.00")
    subscription.document_type = DocumentType.RECEIPT
    invoice = build_invoice(subscription, date(2026, 1, 31), 1)
    assert should_request_allocation(invoice, "000000018") is False


def test_invoice_serialization_roundtrip() -> None:
    invoice = build_invoice(sample_subscription(), date(2026, 1, 31), 1)
    payload = invoice_to_dict(invoice)
    restored = invoice_from_dict(payload)
    assert restored.invoice_id == invoice.invoice_id
    assert restored.total == invoice.total


def test_subscription_serialization_roundtrip() -> None:
    payload = subscription_to_dict(sample_subscription())
    restored = subscription_from_dict(payload)
    assert restored.subscription_id == "SUB-100"
    assert restored.customer.normalized_tax_id() == "514324995"


def test_allocation_payload_shape() -> None:
    invoice = build_invoice(sample_subscription(), date(2026, 1, 31), 1)
    request = AllocationRequest("sandbox", "000000018", invoice, "TX-1", software_id="SW-1")
    payload = create_shaam_allocation_payload(request)
    assert payload["clientTransactionId"] == "TX-1"
    assert payload["invoice"]["amounts"]["subtotal"] == "10000.00"


def test_parse_allocation_response_common_shape() -> None:
    response = parse_allocation_response({"allocationNumber": "2026-ABC", "status": "approved"})
    assert response.allocation_number == "2026-ABC"


def test_parse_allocation_response_official_lowercase_shape() -> None:
    response = parse_allocation_response({"status": 200, "confirmation_number": "2026-LOW", "approved": True})
    assert response.allocation_number == "2026-LOW"


def test_parse_allocation_response_official_titlecase_shape() -> None:
    response = parse_allocation_response({"Status": 200, "Confirmation_Number": "2026-TITLE"})
    assert response.allocation_number == "2026-TITLE"


def test_credit_note_reverses_amounts() -> None:
    invoice = build_invoice(sample_subscription("100.00"), date(2026, 1, 31), 1)
    credit = credit_note_for_invoice(invoice, "Cancellation", 1)
    assert credit.document_type == DocumentType.CREDIT_TAX_INVOICE
    assert credit.total == Decimal("-118.00")


def test_client_create_and_list_subscription() -> None:
    client = RecurringInvoicingClient("000000018")
    created = client.create_subscription(sample_subscription())
    assert created["subscription_id"] == "SUB-100"
    assert len(client.list_subscriptions()) == 1


def test_client_rejects_duplicate_subscription() -> None:
    client = RecurringInvoicingClient("000000018")
    client.create_subscription(sample_subscription())
    with pytest.raises(RecurringInvoiceError):
        client.create_subscription(sample_subscription())


def test_client_pause_and_resume() -> None:
    client = RecurringInvoicingClient("000000018")
    client.create_subscription(sample_subscription())
    assert client.pause_subscription("SUB-100", "non-payment")["status"] == "paused"
    assert client.resume_subscription("SUB-100")["status"] == "active"


def test_client_cancel_sets_end_date() -> None:
    client = RecurringInvoicingClient("000000018")
    client.create_subscription(sample_subscription())
    payload = client.cancel_subscription("SUB-100", date(2026, 3, 31), "requested")
    assert payload["status"] == "cancelled"
    assert payload["end_date"] == "2026-03-31"


def test_client_generate_invoice() -> None:
    client = RecurringInvoicingClient("000000018")
    client.create_subscription(sample_subscription("100.00"))
    invoice = client.generate_invoice("SUB-100", date(2026, 1, 31))
    assert invoice["invoice_id"] == "SUB-100-000001"


def test_client_request_allocation_from_dict() -> None:
    client = RecurringInvoicingClient("000000018", software_id="SW")
    client.create_subscription(sample_subscription())
    invoice = client.generate_invoice("SUB-100", date(2026, 1, 31))
    payload = client.request_allocation(invoice, "TX-2")
    assert payload["business"]["taxId"] == "000000018"


def test_client_submit_allocation_sync() -> None:
    def transport(endpoint: str, payload: dict) -> dict:
        assert endpoint == "/invoices/allocations"
        assert payload["clientTransactionId"] == "TX-3"
        return {"allocationNumber": "ALLOC-3", "status": "approved"}

    client = RecurringInvoicingClient("000000018", sync_transport=transport)
    invoice = build_invoice(sample_subscription(), date(2026, 1, 31), 1)
    response = client.submit_allocation(invoice, "TX-3")
    assert response.allocation_number == "ALLOC-3"


@pytest.mark.asyncio
async def test_client_submit_allocation_async_transport() -> None:
    async def transport(endpoint: str, payload: dict) -> dict:
        assert endpoint == "/invoices/allocations"
        return {"allocationNumber": "ALLOC-4", "status": "approved"}

    client = RecurringInvoicingClient("000000018", async_transport=transport)
    invoice = build_invoice(sample_subscription(), date(2026, 1, 31), 1)
    response = await client.async_submit_allocation(invoice, "TX-4")
    assert response.allocation_number == "ALLOC-4"


@pytest.mark.asyncio
async def test_client_submit_allocation_async_falls_back_to_sync() -> None:
    def transport(endpoint: str, payload: dict) -> dict:
        return {"allocationNumber": "ALLOC-5", "status": "approved"}

    client = RecurringInvoicingClient("000000018", sync_transport=transport)
    invoice = build_invoice(sample_subscription(), date(2026, 1, 31), 1)
    response = await client.async_submit_allocation(invoice, "TX-5")
    assert response.status == "approved"


def test_client_export_import_state(tmp_path: Path) -> None:
    first = RecurringInvoicingClient("000000018")
    first.create_subscription(sample_subscription("100.00"))
    first.generate_invoice("SUB-100", date(2026, 1, 31))
    path = tmp_path / "state.json"
    first.export_state(path)

    second = RecurringInvoicingClient("000000018")
    second.import_state(path)
    invoice = second.generate_invoice("SUB-100", date(2026, 2, 28))
    assert invoice["invoice_id"] == "SUB-100-000002"


def test_allocation_without_transport_raises() -> None:
    client = RecurringInvoicingClient("000000018")
    invoice = build_invoice(sample_subscription(), date(2026, 1, 31), 1)
    with pytest.raises(RecurringInvoiceError):
        client.submit_allocation(invoice, "TX-6")
